import { getSupabaseServer } from '$lib/supabaseServer';
import { fail, redirect } from '@sveltejs/kit';

export const load = async () => {
  const supabaseServer = getSupabaseServer();

  const { data: products, error: pErr } = await supabaseServer
    .from('products')
    .select('*')
    .order('id', { ascending: true });

  if (pErr) {
    throw new Error('Error fetching products: ' + pErr.message);
  }

  return { products };
};

export const actions = {
  default: async ({ request }) => {
    const supabaseServer = getSupabaseServer();
    const form = await request.formData();
    const name = (form.get('name') || '').toString().trim();
    const bar_code = (form.get('bar_code') || '').toString().trim();
    const weightRaw = (form.get('weight') || '').toString().trim();
    const weight = weightRaw === '' ? null : parseFloat(weightRaw);

    if (!name) {
      return fail(400, { error: 'El nombre es obligatorio', values: { name, bar_code, weight } });
    }

    const { data, error } = await supabaseServer
      .from('products')
      .insert([{ name, bar_code: bar_code || null, weight }])
      .select()
      .single();

    if (error) {
      return fail(500, { error: error.message, values: { name, bar_code, weight } });
    }

    throw redirect(303, '/productos');
  }
};
