"""30-day posting queue, Sep 24 - Oct 23 2026. Same tick-and-copy shape as the week plan.

Format mix comes from her own 30-day insights (Aug 25 - Sep 23): Reels 73K views and Posts 72K,
but from far fewer Reels, so Reels earn several posts each. Top two Reels were 55K of 155.8K views
combined. Both were a single line or moment, not a montage. Stories were only 10K against 36K
viewers, which is the biggest unused gap, so there is a story prompt every day.
"""
import json, pathlib

D = [
 ("Thu Sep 24", "9am", "Carousel · 7", "Squeeze — Script vs. Screen", "SQUEEZE AIRED 1993 · 33 YEARS",
  "iCloud › XF Music Videos › <span>Carousel - Script vs Screen (Squeeze)</span>",
  "posted", "Anniversary anchor. Report is live on the site.",
  "Story: the 'where were you' card, then a second slide with your own answer."),
 ("Fri Sep 25", "9am", "Photo", "One rare photo — Lens it first", "",
  "Post Ledger › Rare · unposted", "", "Your 35mm scans post did 8.9K with almost no comments — ask something in the caption.",
  "Story: behind the photo, where it came from."),
 ("Sat Sep 26", "3pm", "REEL", "Ghost Hunting Day \u2014 I went to the Ghosts house", "NATIONAL GHOST HUNTING DAY",
  "Your own footage, Newhall Mansion, Piru CA, 18 Apr 2026 \u00b7 <span>~/Desktop/Ghosts Reel.mp4</span>",
  "", "Replaces the screencap plan written on the 24th. You have been inside the location, which beats stills from the episode. 3pm because Reels in this queue go at 3pm and Saturday mornings are quiet.",
  "Story: poll \u2014 Elegy or Ghosts? Put it up about an hour after the Reel so it points back at it."),
 ("Sun Sep 27", "9am", "Photo", "One rare photo — Lens it first", "",
  "Post Ledger › Rare · unposted", "", "", "Story: one rare photo, no caption, let it sit."),
 ("Mon Sep 28", "9am", "Photo", "Good Neighbor Day — 'Arcadia'", "GOOD NEIGHBOR DAY",
  "Arcadia stills", "", "", "Story: the Arcadia house."),
 ("Tue Sep 29", "—", "Keep light", "A day to keep light. One photo if you feel like it, or nothing.",
  "PERSONAL — NOTHING BIG", "", "", "No launch, no Reel, nothing that needs you online.",
  "Story: skip if you'd rather."),
 ("Wed Sep 30", "3pm", "REEL", "“It's going to be a hell of a series.”", "",
  "S1 gag reel <span>8:52–8:54</span> · David's mock promo, 1993",
  "", "This is the one I'd bet on. He's joking, he's 33 years early, and he was right. Same shape as your 29.3K Reel: one line, no montage.",
  "Story: 'he had no idea' + link sticker to the gag reel page."),
 ("Thu Oct 1", "6–7am", "Photo", "One rare photo — Lens it first", "BACK TO WORK",
  "Post Ledger › Rare · unposted", "", "Schedule it the night before.", "Story: optional."),
 ("Fri Oct 2", "9am", "Photo", "One rare photo — Lens it first", "", "Post Ledger › Rare · unposted", "", "", "Story: one rare photo."),
 ("Sat Oct 3", "9am", "REEL", "“Oh, God, these writers, man.”", "",
  "S6 gag reel <span>5:34–5:36</span>", "", "No profanity, universally relatable, very shareable. Verify the audio first — the transcript is machine-made.",
  "Story: 'which line do you think broke them?'"),
 ("Sun Oct 4", "9am", "Carousel", "Herrenvolk — Script vs. Screen", "HERRENVOLK 30th · S4 PREMIERE",
  "Report already written: <span>tools/comparison-data/herrenvolk.json</span> — I can build the carousel",
  "", "Season 4's 30th starts here and runs all autumn. Your Deep Throat Script vs Screen carousel did 10.8K.",
  "Story: one finding from the report."),
 ("Mon Oct 5", "9am", "Photo", "One rare photo — Lens it first", "", "Post Ledger › Rare · unposted", "", "", "Story: rare photo."),
 ("Tue Oct 6", "3pm", "Site + REEL", "Season 2 gag reel goes live", "",
  "I publish to boggsfiles.com/gag-reels, you post its best line as a Reel",
  "", "Your S1 launch Reel worked. One line, not a montage — the montage version did 4.7K, the line version 29.3K.",
  "Story: link sticker to the new page."),
 ("Wed Oct 7", "9am", "Photo", "One rare photo — Lens it first", "", "Post Ledger › Rare · unposted", "", "", "Story: rare photo."),
 ("Thu Oct 8", "3pm", "REEL", "“What's the line?”", "",
  "S6 gag reel <span>5:44–5:46</span>", "", "Every actor's nightmare, three words. Verify audio.",
  "Story: 'we've all been there'."),
 ("Fri Oct 9", "9am", "Photo", "One rare photo — Lens it first", "", "Post Ledger › Rare · unposted", "", "", "Story: rare photo."),
 ("Sat Oct 10", "9am", "Photo", "One rare photo — Lens it first", "", "Post Ledger › Rare · unposted", "", "", "Story: tease tomorrow."),
 ("Sun Oct 11", "9am", "Carousel", "'Home' — 30 years", "HOME 30th",
  "Stills + the story of the episode Fox banned", "", "'Home' is the most notorious episode of the series. This one has a real ceiling.",
  "Story: 'the one they banned' + poll."),
 ("Mon Oct 12", "9am", "Photo", "One rare photo + tease tomorrow", "",
  "Post Ledger › Rare · unposted", "", "Say X-Files Day is tomorrow.", "Story: countdown sticker."),
 ("Tue Oct 13", "9am + 3pm", "REEL + Carousel", "X-FILES DAY — two posts", "10/13 · CARTER'S + MULDER'S BIRTHDAY",
  "Your single best unposted thing in the morning, carousel in the afternoon",
  "", "The biggest day of the month by a distance. Everyone in the fandom is posting; make yours the one with material nobody else has.",
  "Story: all day. Polls, rare photos, link stickers."),
 ("Wed Oct 14", "9am", "Photo", "One rare photo — Lens it first", "", "Post Ledger › Rare · unposted", "", "", "Story: rare photo."),
 ("Thu Oct 15", "3pm", "Site + REEL", "Season 3 gag reel goes live", "",
  "I publish, you post its best line", "", "", "Story: link sticker."),
 ("Fri Oct 16", "9am", "Photo", "One rare photo — Lens it first", "", "Post Ledger › Rare · unposted", "", "", "Story: rare photo."),
 ("Sat Oct 17", "9am", "REEL", "“Just exactly what are you implying, Agent Scully?”", "",
  "S1 gag reel <span>5:50–5:54</span>", "", "In character, and it lands without profanity.",
  "Story: 'the moose line' setup."),
 ("Sun Oct 18", "9am", "Photo or carousel", "Teliko — 30 years", "TELIKO 30th", "S4 stills", "", "", "Story: rare photo."),
 ("Mon Oct 19", "9am", "Photo", "One rare photo — Lens it first", "", "Post Ledger › Rare · unposted", "", "", "Story: rare photo."),
 ("Tue Oct 20", "9am", "Photo", "One rare photo — Lens it first", "", "Post Ledger › Rare · unposted", "", "", "Story: rare photo."),
 ("Wed Oct 21", "3pm", "REEL", "“He's just too damn good-looking not to be the next king of the big screen.”", "",
  "S4 gag reel <span>5:39–5:44</span>", "", "Verify audio, then let the clip do the work.",
  "Story: 'he wasn't wrong'."),
 ("Thu Oct 22", "3pm", "Site + REEL", "Season 4 gag reel goes live", "",
  "I publish, you post its best line", "", "Season 4's 30th year — tie the caption to it.",
  "Story: link sticker."),
 ("Fri Oct 23", "9am", "Photo", "One rare photo — Lens it first", "", "Post Ledger › Rare · unposted", "",
  "I refresh the next 30 days from your numbers.", "Story: rare photo."),
]

days = [{"id": f"d{i:02d}", "day": d[0], "time": d[1], "kind": d[2], "what": d[3], "note": d[4],
         "file": d[5], "state": d[6], "why": d[7], "story": d[8]} for i, d in enumerate(D, 1)]
pathlib.Path("days.json").write_text(json.dumps(days, ensure_ascii=False))
print(f"{len(days)} days")
print(f"  Reels        : {sum(1 for x in days if 'REEL' in x['kind'])}")
print(f"  photo posts  : {sum(1 for x in days if x['kind']=='Photo')}")
print(f"  carousels    : {sum(1 for x in days if 'Carousel' in x['kind'])}")
