#!/bin/sh

# Configurations
set -e

# Variables
docs_path=$(cd "$(dirname "${BASH_SOURCE:-${0}}")" && pwd -P)
root_path="${docs_path%/*}"

# Prepare cache
rm -f "${docs_path}/.cache/"*.md
mkdir -p "${docs_path}/.cache/"
cp -rfv "${docs_path}/"*.md "${docs_path}/.cache/"

# Export assets
rm -rf "${docs_path}/.cache/assets/images"
mkdir -p "${docs_path}/.cache/assets/images/"
cp -f "${root_path}/docs/preview.svg" "${docs_path}/.cache/assets/images/"

# Export usage
cp -f "${root_path}/README.md" "${docs_path}/.cache/index.md"
sed -i "s#\(\[.*\]\)(.*/docs/#\1(assets/images/#g" "${docs_path}/.cache/index.md"

# Export commits
{
  echo ''
  echo '---'
  echo ''
  cz info | sed \
    -e '1{ /^$/d }' \
    -e '/^</,$ { /^</ { s/^/```powershell\n/ }; ${ s/^/```/ } }' \
    -e 's/^\(- \)\{0,1\}\([a-z0-9 ]\{1,\}\): /\1**`\2`:** /g' \
    -e '/^- /s/ \([Bb]uild\|[Bb]ug[s]*\|[Cc]osmetic\|CI\|[Dd]ocumentation\|[Ff]eature[s]*\|[Ff]ixe[s]*\|[Ii]mprove\|[Ii]ssue[s]*\|[Ll]ocal\|[Nn]either\|[Nn]on-production\|[Pp]erformance\|[Ss]ecurity\|[Tt]emporary\|[Tt]est[s]*\)/ **\1**/g' \
    -e 's/\(A scope\|changed file\|modified feature\|within parenthesis\)/**\1**/g' \
    -e 's/\(e.g.\) \([^.]*\)/\1 `\2`/g' \
    -e 's/\(example:\) \([^)]*\)/**\1** `\2`/g' \
    -e "s/\(BREAKING CHANGE[:]*\)/**\`\1\`**/g" \
    -e 's/\(conventional commits\|semantic versioning\)/**\1**/g' \
    -e "s/ '\([A-Za-z0-9:!]\{1,\}\)' / **\`\1\`** /g" \
    -e 's/^\([^#]\{1,\}\)$/\1  /g' \
    -e '/^[^#\[<-]\{1\}[^`]\{1,\}/s/^/\&nbsp;\&nbsp;\&nbsp;\&nbsp; /g'
  echo ''
  echo '---'
  echo ''
  echo '## Commit example'
  echo ''
  echo '```ruby'
  cz example
  echo '```'
} >>"${docs_path}/.cache/commits.md"

# Export about/changelog
mkdir -p "${docs_path}/.cache/about/"
if ! type git-cliff >/dev/null 2>&1; then
  alias git-cliff='./.tmp/git-cliff'
fi
git-cliff --no-exec --config "${root_path}/config/cliff.toml" --output "${docs_path}/.cache/about/changelog.md"
diff -u "${root_path}/CHANGELOG.md" "${docs_path}/.cache/about/changelog.md" || true

# Export about/license
{
  echo '# License'
  echo ''
  echo '---'
  echo ''
  cat "${root_path}/LICENSE"
} >"${docs_path}/.cache/about/license.md"

# Bind 'md_in_html' extension
sed -i \
  -e 's/<\(details\)>/<\1 markdown>/g' \
  -e 's/<\(div style="padding-left: 30px"\)>/<\1 markdown>/g' \
  -e '/<div style="padding-left: 30px"/{ n; /<br/d; }' \
  "${docs_path}/.cache/"*.md \
  "${docs_path}/.cache/"*/*.md

# Show cache
echo ' '
ls -laR "${docs_path}/.cache/"
echo ' '
