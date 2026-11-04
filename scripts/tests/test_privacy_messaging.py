"""Verify actual bootstrap behavior without external Google network calls."""
from pathlib import Path
import subprocess
import unittest

class PrivacyMessaging(unittest.TestCase):
    def test_pause_precedes_tag_and_consent_never_resumes_ads(self):
        root = Path(__file__).resolve().parents[2]
        path = root / "src/privacy-messaging.js"
        if not path.exists():
            path = root / "assets/privacy-messaging.js"
        subprocess.run(["node", "-e", r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const host = source.match(/const site = "([^"]+)"/)[1];
const publisher = source.match(/const publisher = "([^"]+)"/)[1];
function run(name, existing = false) {
  const scripts = [], entries = [], events = {};
  const win = {location:{hostname:name}};
  const doc = {
    getElementById: () => existing ? {} : null,
    querySelector: () => ({appendChild: x => entries.push(x)}),
    createElement: kind => ({kind,style:{},addEventListener:(name,fn)=>events[name]=fn}),
    head:{appendChild: x => {assert.strictEqual(win.adsbygoogle.pauseAdRequests,1);scripts.push(x);}}
  };
  vm.runInNewContext(source, {window:win,document:doc});
  return {win,scripts,entries,events};
}
for (const name of [host,'www.'+host]) {
  const r=run(name);
  assert.strictEqual(r.scripts.length,1);
  assert.strictEqual(r.scripts[0].src,'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='+publisher);
  assert.strictEqual(r.win.adsbygoogle.length,0);
  assert.strictEqual(r.entries[0].hidden,true);
  const ready=r.win.googlefc.callbackQueue[0].CONSENT_API_READY;
  ready(); // Missing consent API remains harmless and does not reveal a dead control.
  assert.strictEqual(r.entries[0].hidden,true);
  for (const applies of [true,false]) {
    r.win.__tcfapi=(name,version,fn)=>fn({gdprApplies:applies},true);
    ready();
    assert.strictEqual(r.entries[0].hidden,!applies);
  }
  let reopened=0;
  r.win.googlefc.showRevocationMessage=()=>reopened++;
  r.events.click();
  r.win.googlefc.callbackQueue.at(-1)();
  assert.strictEqual(reopened,1);
  assert.strictEqual(r.win.adsbygoogle.pauseAdRequests,1);
  assert.strictEqual(r.win.adsbygoogle.length,0);
}
assert.strictEqual(run('docs.'+host).scripts.length,0);
assert.strictEqual(run('unrelated.example').scripts.length,0);
assert.strictEqual(run(host,true).scripts.length,0);
console.log('PRIVACY_MESSAGING_PAUSED_REQUESTS=PASS');
""", str(path)], check=True, timeout=10)
