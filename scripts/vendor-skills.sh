#!/usr/bin/env bash
# Re-fetches the third-party skills (SKILLS.md) at the pinned commits into
# skills/ (read by .claude/skills and .agents/skills). Run: scripts/vendor-skills.sh
# Needs curl and tar. Nothing else is installed and nothing runs.
set -euo pipefail

SETS=(
  "evaboot-labs/evaboot-plugin 37bb0d5944ab744235a67e62213eb2b70ccc5604 skills define-icp-and-value-prop qualify-leads write-outreach-messages"
  "prosyo-ai/gtm-skill db157476d0eaf40683d3a0c1e906702900206182 skills buying-signal-scoring"
  "anthropics/knowledge-work-plugins 2574e29377c7173d0cecffef29a6ecbd7f8ccb5d sales/skills draft-outreach account-research"
)

cd "$(dirname "$0")/.."
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

for set in "${SETS[@]}"; do
  read -r repo sha base names <<<"$set"
  # names = the rest of the line
  echo "$repo @ ${sha:0:7}"
  curl -fsSL "https://codeload.github.com/$repo/tar.gz/$sha" | tar -xz -C "$tmp"
  root="$tmp/${repo#*/}-$sha"
  for name in $names; do
    [ -d "$root/$base/$name" ] || { echo "missing $base/$name in $repo" >&2; exit 1; }
    rm -rf "skills/$name"
    cp -R "$root/$base/$name" "skills/$name"
    echo "  installed skills/$name"
  done
done
echo "Done. Read each SKILL.md in skills/ before you use it."
