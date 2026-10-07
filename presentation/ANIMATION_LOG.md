# Deck animation test log

Run by `python3 presentation/anim_test.py` (headless Chrome, 1280x720, gated slides included) on 2026-10-07 13:31. Keys: Space with no click steps once, a flood of key events is one step, a click is one step, h shows the help, the page cannot scroll. Each slide: the final state before and after a replay from step 0 must match (at most 0.3 percent of pixels), nothing left running or hidden, auto time at most 3000 ms. Run it alone: two programs driving the browser at once break each other's sessions.

```
PASS keys: Space with no click is step 1 of slide 1
PASS keys: a flood of 100 Space events moves at most one step
PASS keys: a click is one step, then ArrowRight one more step: no skipping
PASS keys: Left goes back one step
PASS keys: h shows the one-line help
PASS keys: the page cannot scroll (overflow hidden)
PASS  1 the-call                                   steps=4 auto=1921ms diff=0.000% running=0 hidden=0
PASS  2 the-name                                   steps=0 auto=0ms diff=0.000% running=0 hidden=0
PASS  3 one-engine                                 steps=2 auto=1860ms diff=0.000% running=0 hidden=0
PASS  4 the-demo                                   steps=3 auto=2274ms diff=0.000% running=0 hidden=0
PASS  5 what-the-family-gets                       steps=3 auto=1383ms diff=0.000% running=0 hidden=0
PASS  6 built-to-grow                              steps=3 auto=1964ms diff=0.000% running=0 hidden=0
PASS  7 how-it-is-built                            steps=3 auto=1583ms diff=0.000% running=0 hidden=0
PASS  8 use-of-ai                                  steps=4 auto=2416ms diff=0.000% running=0 hidden=0
PASS  9 the-evaluation-system                      steps=3 auto=1865ms diff=0.000% running=0 hidden=0
PASS 10 impact                                     steps=2 auto=1346ms diff=0.000% running=0 hidden=0
PASS 11 what-we-built                              steps=4 auto=1671ms diff=0.000% running=0 hidden=0
PASS 12 close                                      steps=2 auto=1383ms diff=0.000% running=0 hidden=0
PASS 13 the-evaluation-system-in-detail            steps=1 auto=539ms diff=0.000% running=0 hidden=0
PASS 14 what-broke-and-what-changed                steps=1 auto=455ms diff=0.000% running=0 hidden=0
PASS 15 jev-checks-every-draft                     steps=1 auto=538ms diff=0.000% running=0 hidden=0
PASS 16 does-nury-learn-from-pastors               steps=1 auto=538ms diff=0.000% running=0 hidden=0
PASS 17 four-test-layers-before-release-never-at   steps=1 auto=463ms diff=0.000% running=0 hidden=0
PASS 18 privacy-that-is-tested                     steps=1 auto=539ms diff=0.000% running=0 hidden=0
PASS 19 cases-export-and-pdf                       steps=1 auto=542ms diff=0.000% running=0 hidden=0
PASS 20 listed-does-not-mean-recommended           steps=1 auto=453ms diff=0.000% running=0 hidden=0
PASS 21 informed-by-case-management-practice       steps=1 auto=467ms diff=0.000% running=0 hidden=0
PASS 22 where-nury-fits                            steps=1 auto=460ms diff=0.000% running=0 hidden=0
PASS 23 credits                                    steps=1 auto=537ms diff=0.000% running=0 hidden=0
ALL PASS
```
