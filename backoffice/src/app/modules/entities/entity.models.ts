export interface SchemaColumn {
  name: string;
  type: string;
  db_type: string;
  length: number | null;
  precision: number | null;
  scale: number | null;
  nullable: boolean;
  primary_key: boolean;
  default: unknown;
}

export interface SchemaTable {
  name: string;
  columns: SchemaColumn[];
  indexes: { name: string; columns: string[]; unique: boolean }[];
}
