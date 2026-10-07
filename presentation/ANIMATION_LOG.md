# Deck animation test log

Run by `python3 presentation/anim_test.py` (headless Chrome, 1280x720, gated slides included) on 2026-10-07 13:27. Keys: Space with no click steps once, a flood of key events is one step, a click is one step, h shows the help, the page cannot scroll. Each slide: the final state before and after a replay from step 0 must match (at most 0.3 percent of pixels), nothing left running or hidden, auto time at most 3000 ms. Run it alone: two programs driving the browser at once break each other's sessions.

```
PASS keys: Space with no click is step 1 of slide 1
PASS keys: a flood of 100 Space events moves at most one step
PASS keys: a click is one step, then ArrowRight one more step: no skipping
PASS keys: Left goes back one step
PASS keys: h shows the one-line help
PASS keys: the page cannot scroll (overflow hidden)
PASS  1 the-call                                   steps=4 auto=1931ms diff=0.000% running=0 hidden=0
PASS  2 the-name                                   steps=0 auto=0ms diff=0.000% running=0 hidden=0
PASS  3 one-engine                                 steps=2 auto=1865ms diff=0.000% running=0 hidden=0
PASS  4 the-demo                                   steps=3 auto=2281ms diff=0.000% running=0 hidden=0
PASS  5 what-the-family-gets                       steps=3 auto=1379ms diff=0.000% running=0 hidden=0
PASS  6 built-to-grow                              steps=3 auto=1964ms diff=0.000% running=0 hidden=0
PASS  7 how-it-is-built                            steps=3 auto=1610ms diff=0.000% running=0 hidden=0
PASS  8 use-of-ai                                  steps=4 auto=2415ms diff=0.000% running=0 hidden=0
PASS  9 the-evaluation-system                      steps=3 auto=1877ms diff=0.000% running=0 hidden=0
PASS 10 impact                                     steps=2 auto=1344ms diff=0.000% running=0 hidden=0
PASS 11 what-we-built                              steps=4 auto=1683ms diff=0.000% running=0 hidden=0
PASS 12 close                                      steps=2 auto=1390ms diff=0.000% running=0 hidden=0
PASS 13 memorial                                   steps=0 auto=0ms diff=0.000% running=0 hidden=0
PASS 14 the-evaluation-system-in-detail            steps=1 auto=540ms diff=0.000% running=0 hidden=0
PASS 15 what-broke-and-what-changed                steps=1 auto=461ms diff=0.000% running=0 hidden=0
PASS 16 jev-checks-every-draft                     steps=1 auto=538ms diff=0.000% running=0 hidden=0
PASS 17 does-nury-learn-from-pastors               steps=1 auto=536ms diff=0.000% running=0 hidden=0
PASS 18 four-test-layers-before-release-never-at   steps=1 auto=514ms diff=0.000% running=0 hidden=0
PASS 19 privacy-that-is-tested                     steps=1 auto=542ms diff=0.000% running=0 hidden=0
PASS 20 cases-export-and-pdf                       steps=1 auto=541ms diff=0.000% running=0 hidden=0
PASS 21 listed-does-not-mean-recommended           steps=1 auto=445ms diff=0.000% running=0 hidden=0
PASS 22 informed-by-case-management-practice       steps=1 auto=502ms diff=0.000% running=0 hidden=0
PASS 23 where-nury-fits                            steps=1 auto=447ms diff=0.000% running=0 hidden=0
PASS 24 credits                                    steps=1 auto=555ms diff=0.000% running=0 hidden=0
ALL PASS
```
