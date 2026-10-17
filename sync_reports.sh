#!/usr/bin/env bash
# مزامنة كل التقارير على جهازك بضغطة واحدة.
# الاستخدام: من داخل فولدر المشروع شغّل:  bash sync_reports.sh
set -e
BRANCH="ccr-5df15efa-8lfmux"

echo "⬇️  بجيب آخر نسخة من الفرع: $BRANCH ..."
git fetch origin "$BRANCH"

# لو مش على نفس الفرع، انتقل له (آمن: مش بيمسح شغلك المحلي)
CUR="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CUR" != "$BRANCH" ]; then
  git checkout "$BRANCH"
fi

git pull origin "$BRANCH"

echo ""
echo "✅ تم. كل التقارير محدّثة على جهازك في: $(pwd)/Reports"
echo "📄 الفهرس الشامل: Reports/00_الفهرس_الشامل.md"
echo ""

# افتح فولدر التقارير (اختياري — يشتغل على ماك/ويندوز/لينكس)
if command -v open >/dev/null 2>&1; then open Reports            # macOS
elif command -v explorer.exe >/dev/null 2>&1; then explorer.exe Reports  # Windows (Git Bash/WSL)
elif command -v xdg-open >/dev/null 2>&1; then xdg-open Reports  # Linux
fi
