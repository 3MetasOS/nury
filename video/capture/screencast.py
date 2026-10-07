"""True-phone screen recording at 2x: viewport 390x844 with device_scale_factor 2, frames from the Chrome DevTools screencast (about 30 fps),
assembled with ffmpeg into a 780x1688 30 fps MP4. (Playwright's own video recorder ignores the scale factor, and the html zoom trick changes the layout.)"""
import base64, subprocess, tempfile, time
from pathlib import Path

class Cast:
    def __init__(self, ctx, page):
        self.page = page; self.cdp = ctx.new_cdp_session(page); self.frames = []; self.dir = Path(tempfile.mkdtemp(prefix="cast_")); self.t0 = None
        self.cdp.on("Page.screencastFrame", self._on)
    def _on(self, ev):
        ts = ev["metadata"]["timestamp"] - self.wall0  # the frame's own epoch timestamp; marks use time.time(), the same clock
        p = self.dir / f"{len(self.frames):06d}.jpg"; p.write_bytes(base64.b64decode(ev["data"])); self.frames.append((ts, p))
        try: self.cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
        except Exception: pass
    def start(self):
        self.wall0 = time.time(); self.cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": 780, "maxHeight": 1688, "everyNthFrame": 1})
    def now(self): return time.time() - self.wall0   # approximate seconds since start (use for marks)
    def stop(self, out_mp4):
        end = self.now(); self.cdp.send("Page.stopScreencast"); fr = [(0.0 if i == 0 else t, p) for i, (t, p) in enumerate(self.frames)]
        lst = self.dir / "list.txt"
        with open(lst, "w") as f:
            for i, (t, p) in enumerate(fr):
                d = (fr[i + 1][0] - t) if i + 1 < len(fr) else max(end - t, 0.1)
                f.write(f"file '{p}'\nduration {max(d, 0.001):.4f}\n")
            f.write(f"file '{fr[-1][1]}'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", "fps=30,scale=780:1688:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "14", "-an", str(out_mp4)], check=True)
        return len(fr)
