#!/usr/bin/env python3
"""
x_grok_bridge.py — Talk to Grok on X (Twitter) via Safari automation

X 上的 Grok 对 X 平台数据有更强的访问能力（热点、帖子、趋势等）。

前置条件:
  Safari > 设置 > 高级 > 显示网页开发者功能 ✓
  Safari > 开发 > 允许来自 Apple Events 的 JavaScript ✓
  Safari 已登录 x.com

用法:
  python3 x_grok_bridge.py --port 19999
  curl --noproxy localhost -X POST http://localhost:19999/chat -H "Content-Type: application/json" -d '{"prompt":"今天X上最热的话题是什么？"}'
"""
import json, time, threading, re, argparse, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

X_GROK_URL = 'https://x.com/i/grok'
VERSION = 'v1'
INPUT_SEL = 'textarea[placeholder="Ask anything"]'
SEND_SEL = 'button[aria-label="Grok something"]'


class XGrokBridge:
    def __init__(self):
        self.lock = threading.Lock()

    def _osa(self, script, timeout=30):
        r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            raise RuntimeError(f'osascript: {r.stderr.strip()[:200]}')
        return r.stdout.strip()

    def _js(self, js, timeout=30):
        esc = js.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return self._osa(f'tell application "Safari" to do JavaScript "{esc}" in current tab of front window', timeout)

    def _ensure_x_grok(self):
        try:
            url = self._osa('tell application "Safari" to get URL of current tab of front window')
        except:
            url = ''
        if 'x.com/i/grok' not in url:
            self._osa(f'tell application "Safari" to set URL of current tab of front window to "{X_GROK_URL}"')
            time.sleep(4)

    def _find_input(self):
        r = self._js(f"document.querySelector('{INPUT_SEL}') ? 'yes' : 'no'")
        return INPUT_SEL if r == 'yes' else None

    def _wait_ready(self, timeout=20):
        start = time.time()
        while time.time() - start < timeout:
            if self._find_input():
                return INPUT_SEL
            time.sleep(0.5)
        return None

    def _type_and_send(self, text):
        self._osa('tell application "Safari" to activate')
        time.sleep(0.3)
        safe = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')
        self._js(f"""(function(){{
            var ta = document.querySelector('{INPUT_SEL}');
            if (!ta) return 'NO INPUT';
            ta.focus();
            document.execCommand('selectAll', false);
            document.execCommand('insertText', false, '{safe}');
            return 'OK';
        }})()""")
        time.sleep(0.5)
        # Click "Grok something" submit button
        r = self._js(f"""(function(){{
            var btn = document.querySelector('{SEND_SEL}');
            if (btn && !btn.disabled) {{ btn.click(); return 'OK'; }}
            return 'NO BTN';
        }})()""")
        if r == 'OK':
            return True
        # Fallback: Enter key
        self._js(f"document.querySelector('{INPUT_SEL}')?.dispatchEvent(new KeyboardEvent('keydown',{{key:'Enter',keyCode:13,bubbles:true}}))")
        return True

    def _get_body(self):
        return self._js('document.body.innerText', timeout=15)

    def _clean(self, text):
        # Remove X/Grok UI artifacts
        for marker in ['\nAsk anything', '\nGrok something', '\nFocus Mode',
                        '\nChat history', '\nPrivate\n', '\nExplore\n',
                        '\nCreate Images\n', '\nLatest News\n', '\nAuto\n']:
            i = text.rfind(marker)
            if i > 0:
                text = text[:i]
        text = re.sub(r'\n[0-9]+(\.[0-9]+)?s\n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _extract(self, body, prompt):
        marker = prompt[:60]
        parts = body.split(marker)
        after = parts[-1] if len(parts) >= 2 else body
        return self._clean(after)

    def chat(self, prompt, timeout=120):
        with self.lock:
            return self._chat(prompt, timeout)

    def _chat(self, prompt, timeout):
        try:
            self._ensure_x_grok()
            sel = self._wait_ready()
            if not sel:
                return {'status': 'error', 'error': 'input not found — is Safari on x.com/i/grok?'}
            body_before = self._get_body()
            self._type_and_send(prompt)
            # Poll for stable response
            start = time.time()
            last = ''
            stable = 0
            while time.time() - start < timeout:
                time.sleep(2)
                body = self._get_body()
                if body != body_before and body == last:
                    stable += 1
                    if stable >= 3:
                        return {
                            'status': 'ok',
                            'response': self._extract(body, prompt),
                            'elapsed': round(time.time() - start, 1)
                        }
                else:
                    stable = 0
                last = body
            resp = self._extract(last, prompt) if last else ''
            return {'status': 'timeout', 'response': resp, 'elapsed': round(time.time() - start, 1)}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def new_conversation(self):
        try:
            self._osa(f'tell application "Safari" to set URL of current tab of front window to "{X_GROK_URL}"')
            time.sleep(3)
            return {'status': 'ok'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def history(self):
        try:
            body = self._get_body()
            return {'status': 'ok', 'content': self._clean(body), 'raw_length': len(body)}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def health(self):
        try:
            url = self._osa('tell application "Safari" to get URL of current tab of front window')
            return {'status': 'ok', 'url': url, 'on_x_grok': 'x.com/i/grok' in url, 'version': VERSION}
        except:
            return {'status': 'error', 'error': 'safari not reachable', 'version': VERSION}


bridge = None


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
        if self.path == '/chat':
            p = data.get('prompt', '')
            to = data.get('timeout', 120)
            ts = time.strftime('%H:%M:%S')
            print(f'[{ts}] >> {p[:80]}', flush=True)
            try:
                r = bridge.chat(p, to)
                self._json(200, r)
                print(f'[{ts}] << [{r.get("status")}] {str(r.get("response", r.get("error", "")))[:80]}', flush=True)
            except Exception as e:
                self._json(500, {'error': str(e), 'status': 'error'})
        elif self.path == '/new':
            try:
                self._json(200, bridge.new_conversation())
            except Exception as e:
                self._json(500, {'error': str(e), 'status': 'error'})
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self._json(200, bridge.health())
        elif self.path == '/history':
            try:
                self._json(200, bridge.history())
            except Exception as e:
                self._json(500, {'error': str(e), 'status': 'error'})
        else:
            self.send_response(404)
            self.end_headers()

    def _json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, *a):
        pass


class ThreadedServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


if __name__ == '__main__':
    pa = argparse.ArgumentParser()
    pa.add_argument('--port', type=int, default=19999)
    a = pa.parse_args()
    bridge = XGrokBridge()
    print(f'X Grok Bridge {VERSION} :{a.port}', flush=True)
    print('前置: Safari > 开发 > 允许来自 Apple Events 的 JavaScript', flush=True)
    print(f'前置: Safari 已登录 x.com', flush=True)
    ThreadedServer(('0.0.0.0', a.port), Handler).serve_forever()
