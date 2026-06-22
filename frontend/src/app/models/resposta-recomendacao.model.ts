import { MusicaRecomendada } from "./musica-recomendada.model";


export interface RespostaRecomendacao {
  modo: string;
  genero_detectado: string;
  musica_buscada: MusicaRecomendada | null;
  recomendacoes: MusicaRecomendada[];
}

