# Choose install location (Homebrew bin dir)
BIN_DIR="$(brew --prefix)/bin"
# sudo mkdir -p "$BIN_DIR"

# Pick platform based on your Mac
ARCH="$(uname -m)"
if [ "$ARCH" = "arm64" ]; then
  PLATFORM="mac-arm64"
else
  PLATFORM="mac-x64"
fi
echo "ARCH=$ARCH PLATFORM=$PLATFORM"

# Get latest patch version for milestone 145
VER="$(curl -fsSL https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_146)"
echo "ChromeDriver milestone 145 version: $VER"

# Download + install
URL="https://storage.googleapis.com/chrome-for-testing-public/${VER}/${PLATFORM}/chromedriver-${PLATFORM}.zip"
echo "Downloading: $URL"

TMPDIR="$(mktemp -d)"
curl -fL "$URL" -o "$TMPDIR/chromedriver.zip"
unzip -q "$TMPDIR/chromedriver.zip" -d "$TMPDIR"

install -m 0755 "$TMPDIR/chromedriver-${PLATFORM}/chromedriver" "$BIN_DIR/chromedriver"

# Verify
which chromedriver
chromedriver --version