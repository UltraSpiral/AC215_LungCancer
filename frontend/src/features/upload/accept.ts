export const ACCEPTED_EXTENSIONS = ['.svs'];

/** The model server accepts Aperio .svs whole-slide images only. */
export function isAcceptedSlide(file: File): boolean {
  const name = file.name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((ext) => name.endsWith(ext));
}
