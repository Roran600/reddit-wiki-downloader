#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.backup.pid"

cleanup() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo ""
            echo "[*] Gracefulne ukoncujem backup (PID: $PID)..."
            kill -INT "$PID" 2>/dev/null

            for i in {1..10}; do
                if ! kill -0 "$PID" 2>/dev/null; then
                    echo "[✓] Backup ukonceny"
                    break
                fi
                sleep 1
            done

            if kill -0 "$PID" 2>/dev/null; then
                echo "[!] Nucene ukoncujem..."
                kill -9 "$PID" 2>/dev/null
            fi
        fi
        rm -f "$PID_FILE"
    fi
}

trap cleanup EXIT INT TERM

cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "[-] Virtuálne prostredie 'venv' neexistuje!"
    echo "    Spust: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

echo "[*] Aktivujem virtualne prostredie..."
source venv/bin/activate

echo "[*] Spustam backup..."
python backup.py &
BACKUP_PID=$!
echo "$BACKUP_PID" > "$PID_FILE"

echo "[*] Backup bezi (PID: $BACKUP_PID)"
echo "[*] Pre ukoncenie stlac Ctrl+C"

wait $BACKUP_PID
EXIT_CODE=$?

rm -f "$PID_FILE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "[✓] Backup dokonceny uspesne"
else
    echo "[!] Backup ukonceny s chybou (exit code: $EXIT_CODE)"
fi

exit $EXIT_CODE