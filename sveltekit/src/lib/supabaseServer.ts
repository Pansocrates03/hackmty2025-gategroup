import pkg from '@supabase/supabase-js';
const { createClient } = pkg;
import { env } from '$env/dynamic/private';

// Do NOT create the client at module evaluation time. Instead expose a getter
// that creates the client at runtime (server) so builds without env vars succeed.
export function getSupabaseServer() {
  const url = env.SUPABASE_URL;
  const key = env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) {
    throw new Error('Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables');
  }

  return createClient(url, key, { auth: { persistSession: false } });
}

export default getSupabaseServer;
