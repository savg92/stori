#!/bin/sh
set -e

# Replace environment variables in JavaScript files
if [ -n "$VITE_SUPABASE_URL" ]; then
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|VITE_SUPABASE_URL_PLACEHOLDER|$VITE_SUPABASE_URL|g" {} \;
fi

if [ -n "$VITE_SUPABASE_ANON_KEY" ]; then
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|VITE_SUPABASE_ANON_KEY_PLACEHOLDER|$VITE_SUPABASE_ANON_KEY|g" {} \;
fi

if [ -n "$VITE_API_BASE_URL" ]; then
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|VITE_API_BASE_URL_PLACEHOLDER|$VITE_API_BASE_URL|g" {} \;
fi

echo "🚀 Frontend container starting..."
echo "📝 Environment variables substituted"
echo "🌐 Ready to serve on port 80"

# Execute the CMD
exec "$@"