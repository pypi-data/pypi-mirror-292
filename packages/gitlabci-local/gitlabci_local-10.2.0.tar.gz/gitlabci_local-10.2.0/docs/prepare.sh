#!/bin/sh

# Configurations
set -e

# Variables
docs_path=$(cd "$(dirname "${BASH_SOURCE:-${0}}")" && pwd -P)
root_path="${docs_path%/*}"

# Prepare cache
rm -f "${docs_path}/.cache/*.md"
mkdir -p "${docs_path}/.cache/"
cp -rfv "${docs_path}/"*.md "${docs_path}/.cache/"

# Export assets
rm -rf "${docs_path}/.cache/assets/images"
mkdir -p "${docs_path}/.cache/assets/images/"
cp -f "${root_path}/docs/preview.svg" "${docs_path}/.cache/assets/images/"

# Export usage
cp -f "${root_path}/README.md" "${docs_path}/.cache/index.md"
sed -i "s#\(\[.*\]\)(.*/docs/#\1(assets/images/#g" "${docs_path}/.cache/index.md"

# Export about/changelog
mkdir -p "${docs_path}/.cache/about/"
cp -f "${root_path}/CHANGELOG.md" "${docs_path}/.cache/about/changelog.md"

# Export about/license
{
  echo '# License'
  echo ''
  echo '---'
  echo ''
  cat "${root_path}/LICENSE"
} >"${docs_path}/.cache/about/license.md"

# Show cache
echo ' '
ls -laR "${docs_path}/.cache/"
echo ' '
