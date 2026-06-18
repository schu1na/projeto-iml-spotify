import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { RespostaRecomendacao } from '../models/resposta-recomendacao.model';
import { AudioFeatures } from '../models/audio-features.model';

@Injectable({
  providedIn: 'root'
})
export class RecomendacaoService {
  // A URL exata onde o seu FastAPI está rodando localmente
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) { }

  // Função que envia o POST para o Python
  obterRecomendacoes(features: AudioFeatures, usarFiltro: boolean = true): Observable<RespostaRecomendacao> {
    const corpoRequisicao = {
      audio_features: features,
      filtrar_genero: usarFiltro
    };

    return this.http.post<RespostaRecomendacao>(`${this.apiUrl}/recomendar`, corpoRequisicao);
  }

  buscarSugestoes(texto: string): Observable<any[]> {
    const url = `${this.apiUrl}/buscar-sugestoes?texto_busca=${encodeURIComponent(texto)}`;
    return this.http.get<any[]>(url);
  }

  buscarAudioFeatures(trackId: string): Observable<any> {
    const url = `${this.apiUrl}/buscar-audio-features?track_id=${trackId}`;
    return this.http.get<any>(url);
  }
}