# Collection layout preference

Always center incomplete final rows of cards across scripts, transcripts, comparisons, and other collection pages. Keep cards the same width as the complete rows. Never leave a filled background block in unused columns.

The shared collection rules in `dist/assets/site-header.css` implement this for current card collections at desktop and mobile widths. Reuse an existing collection class for new collections, or add its selector and responsive column counts to that shared rule. Keep intentionally mixed editorial layouts separate. Script episode, schedule and call-sheet grids already use centered final-row grid rules in `archive-detail.css`.
