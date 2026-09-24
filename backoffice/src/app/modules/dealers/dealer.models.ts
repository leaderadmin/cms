export type DealerType = 'branch' | 'atm' | 'transaction_office';
export interface Dealer { id: number; name: string; code: string; dealer_type: DealerType; province_city: string; address: string; hotline: string; email: string; latitude: string | null; longitude: string | null; opening_hours: string; status: number; area_id: number | null; area: string; region_id: number | null; region: string; }
export type DealerInput = Omit<Dealer, 'id'>;
