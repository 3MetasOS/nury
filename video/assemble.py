#!/usr/bin/env python3
"""ffmpeg fallback cut of the 90 s demo (no Remotion). Same scene table as remotion/src/Nury.tsx.
Needs: remotion/public/{run.mp4,marks.json,vo/*.wav} (run remotion/prep.sh), cards/out/end.png (python cards/render.py).
Usage: python3 assemble.py [out.mp4]"""
import json, subprocess, sys, tempfile, os
from pathlib import Path
H = Path(__file__).resolve().parent; P = H / "remotion/public"; OUT = sys.argv[1] if len(sys.argv) > 1 else str(H / "out_ffmpeg.mp4")
M = json.load(open(P / "marks.json"))
VO = {'01':'It is two in the morning. A family is calling their pastor.','02':'Her husband was detained last evening. The pastor has no staff, and no lawyer on the line.','03':'Nury turns the call into a clear case. Facts only. No advice.','04':'After every stage, the pastor decides.','05':"Rights in the family's own language. Built only from a vetted source. Every point cited.",'06':'When a draft crosses the line from information into advice, Nury rejects it and tries again. The pastor never sees it.','07':'Attorney hotlines. A checklist for tonight.','08':"And a short, warm message, in the pastor's hands to edit.",'09':'Nury is not a pastor, and it never sends. The pastor does.','10':'Nury. The crisis-response agent for solo pastors.'}
VOLEN = {'01':3.56,'02':5.79,'03':4.79,'04':2.96,'05':5.67,'06':7.5,'07':3.05,'08':3.9,'09':4.18,'10':3.78}
S = [  # id, kind, dur, from, to, label, vo[(key, at)]
 ('lock','lock',9,None,None,None,[('01',1.5)]),
 ('selector','clip',4,('selector',0),('selector',3.7),'The pastor picks the crisis.',[]),
 ('intake','clip',6,('selector',3.7),('start',0.3),'Solo pastor. No staff. No lawyer.',[('02',0.3)]),
 ('triage','clip',11,('start',0.3),('approve1',0.4),'1  Triage',[('03',4.5),('04',8.2)]),
 ('rights','clip',18,('approve1',0.4),('approve2',0.4),'2  Rights brief. Vetted sources only.',[('05',6),('06',10.5)]),
 ('montage','clip',12,('approve2',0.4),('approve4',0.4),'3  Attorneys   4  Checklist',[('07',4)]),
 ('pastoral','clip',11,('approve4',0.4),('approve5',0.4),'5  Pastoral message',[('08',3)]),
 ('package','clip',11,('approve5',0.4),('end',0),'Nury does not send. The pastor does.',[('09',1)]),
 ('end','end',8,None,None,None,[('10',1)])]
GEO = '/System/Library/Fonts/Supplemental/Georgia.ttf'; HEL = '/System/Library/Fonts/Helvetica.ttc'
esc = lambda t: t.replace("\\","\\\\").replace(":","\\:").replace("'","\u2019").replace("%","\\%")
tmp = Path(tempfile.mkdtemp()); segs = []; audio = []; t0 = 0.0
def run(a): subprocess.run(["ffmpeg","-y","-loglevel","error",*a], check=True)
for i,(sid,kind,dur,fr,to,label,vo) in enumerate(S):
    out = tmp / f"{i:02d}.mp4"; bg = f"color=c=0xf7f3ea:s=1920x1080:r=30:d={dur}"
    caps = "".join(f",drawtext=fontfile={HEL}:text='{esc(VO[k])}':fontsize=34:fontcolor=0x0d1015:box=1:boxcolor=0xf7f3ea@0.94:boxborderw=12:x=(w-text_w)/2:y=h-90:enable='between(t,{at},{at+VOLEN[k]+0.5})'" for k,at in vo)
    fade = f",fade=t=in:d=0.33,fade=t=out:st={dur-0.33}:d=0.33"
    if kind == 'clip':
        a = M[fr[0]]+fr[1]; b = M[to[0]]+to[1]; rate = min(4,max(0.85,(b-a)/dur))
        lab = f",drawtext=fontfile={GEO}:text='{esc(label)}':fontsize=64:fontcolor=0x0d1015:x=1110:y=(h-text_h)/2" if label else ""
        fc = f"[1:v]setpts=PTS/{rate},scale=-2:900[p];[0:v][p]overlay=470:40:eof_action=repeat{lab}{caps}{fade}[v]"
        run(["-f","lavfi","-i",bg,"-ss",f"{a}","-t",f"{b-a}","-i",str(P/"run.mp4"),"-filter_complex",fc,"-map","[v]","-t",f"{dur}","-pix_fmt","yuv420p",str(out)])
    elif kind == 'lock':
        fc = f"[0:v]drawbox=x=745:y=100:w=430:h=880:color=0x080a0e:t=fill,drawtext=fontfile={GEO}:text='2\\:07':fontsize=140:fontcolor=0xece7dc:x=(w-text_w)/2:y=330,drawtext=fontfile={HEL}:text='AM':fontsize=30:fontcolor=0xa79f8d:x=(w-text_w)/2:y=490,drawtext=fontfile={GEO}:text='Maria':fontsize=52:fontcolor=0xece7dc:x=(w-text_w)/2:y=600,drawtext=fontfile={HEL}:text='calling':fontsize=28:fontcolor=0xe8a33d:x=(w-text_w)/2:y=670{caps}{fade}[v]"
        run(["-f","lavfi","-i",bg,"-filter_complex",fc,"-map","[v]","-t",f"{dur}","-pix_fmt","yuv420p",str(out)])
    else:
        fc = f"[0:v]null{caps}{fade}[v]"
        run(["-loop","1","-framerate","30","-i",str(H/"cards/out/end.png"),"-filter_complex",fc,"-map","[v]","-t",f"{dur}","-pix_fmt","yuv420p",str(out)])
    segs.append(out); audio += [(k, t0+at) for k,at in vo]; t0 += dur
lst = tmp/"list.txt"; lst.write_text("".join(f"file '{s}'\n" for s in segs))
vid = tmp/"video.mp4"; run(["-f","concat","-safe","0","-i",str(lst),"-c","copy",str(vid)])
ins = []; fl = []
for n,(k,t) in enumerate(audio): ins += ["-i",str(P/f"vo/{k}.wav")]; fl.append(f"[{n+1}:a]adelay={int(t*1000)}|{int(t*1000)}[a{n}]")
fl.append("".join(f"[a{n}]" for n in range(len(audio)))+f"amix=inputs={len(audio)}:normalize=0[aout]")
run(["-i",str(vid),*ins,"-filter_complex",";".join(fl),"-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-t",f"{t0}",OUT])
print(OUT, f"{t0:.1f}s")
for sg in segs: print(sg.name, subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(sg)],capture_output=True,text=True).stdout.strip())
