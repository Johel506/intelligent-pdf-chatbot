import enTranslations from '../locales/en.json';

export const t = (key) => {
  return enTranslations[key] || key;
}; 