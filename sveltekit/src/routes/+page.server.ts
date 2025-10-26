import { getSupabaseServer } from '$lib/supabaseServer';
import { fail, redirect } from '@sveltejs/kit';

export const load = async () => {
  try {
    const supabaseServer = getSupabaseServer();

    // Cargar productos
    const { data: products, error: pErr } = await supabaseServer
      .from('products')
      .select('*')
      .order('id', { ascending: true });

    // Cargar productos devueltos
    const { data: returned_products, error: rErr } = await supabaseServer
      .from('returned_products')
      .select('*')
      .order('id', { ascending: true });

    // Cargar trolleys
    const { data: trolleys, error: tErr } = await supabaseServer
      .from('trolleys')
      .select('*')
      .order('updated_at', { ascending: false });

    if (pErr || rErr || tErr) {
      console.error('Error fetching data from Supabase:', pErr ?? rErr ?? tErr);
      return {
        products: products ?? [],
        returned_products: returned_products ?? [],
        trolleys: trolleys ?? []
      };
    }

    return {
      products: products ?? [],
      returned_products: returned_products ?? [],
      trolleys: trolleys ?? []
    };
  } catch (err) {
    console.error('Root +page.server load error:', err);
    // Devuelve arrays vacíos como fallback para evitar 500 en SSR
    return {
      products: [],
      returned_products: [],
      trolleys: []
    };
  }
};