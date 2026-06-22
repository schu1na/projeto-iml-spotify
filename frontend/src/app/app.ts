import { Component, signal } from '@angular/core';
import { SearchBar } from './components/search-bar/search-bar';
import { MusicCard } from './components/music-card/music-card';
import { ThemeService } from './services/theme.service';
import { SugestaoMusica } from './models/sugestao-musica.model';
import { MusicaRecomendada } from './models/musica-recomendada.model';
import { RecomendacaoService } from './services/recomendacao.service';
import { AudioFeatures } from './models/audio-features.model';
import { switchMap } from 'rxjs';
import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'app-root',
  imports: [SearchBar, MusicCard, DecimalPipe],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  constructor(
    public themeService: ThemeService,
    private recomendacaoService: RecomendacaoService
  ) { }

  protected readonly hasSearched = signal(false);
  protected readonly searchedQuery = signal<SugestaoMusica | null>(null);
  protected readonly isLoading = signal(false);
  protected readonly musicaBuscada = signal<MusicaRecomendada | null>(null);
  protected readonly generoObtido = signal<string>("");

  private filtrarBuscaPorGenero: boolean = false;
  private motorClassificacao: string = 'lightgbm';

  featuresAtuais: AudioFeatures | null = null;
  protected readonly musicasRecomendadas = signal<MusicaRecomendada[]>([]);

  onSearch(query: SugestaoMusica): void {
    this.isLoading.set(true);
    this.searchedQuery.set(query);

    // 1. Inicia a primeira chamada
    this.recomendacaoService.buscarAudioFeatures(query.id).pipe(
      
      // 2. Assim que a primeira terminar, o switchMap entra em ação
      switchMap((features: AudioFeatures) => {
        console.log('Audio Features:', features);
        this.featuresAtuais = features; // Salva se precisar usar em outro lugar
        
        // Dispara a segunda chamada, usando o resultado da primeira
        console.log(query.id)
        return this.recomendacaoService.obterRecomendacoes(
          query.id,
          features,
          this.filtrarBuscaPorGenero,
          this.motorClassificacao
        );
      })

    ).subscribe({
      // 3. Este 'next' só é chamado quando a SEGUNDA requisição terminar!
      next: (response) => {
        this.musicaBuscada.set(response.musica_buscada);
        this.generoObtido.set(response.genero_detectado);
        this.musicasRecomendadas.set(response.recomendacoes);
        this.hasSearched.set(true);
        this.isLoading.set(false);
      },
      // Este 'error' captura falhas de QUALQUER UMA das duas requisições
      error: (error) => {
        console.error('Erro no fluxo de busca:', error);
        this.isLoading.set(false); // Importante para não deixar a tela travada carregando!
      }
    });
  }

  onFiltroGenero(value: boolean) {
    this.filtrarBuscaPorGenero = value;
  }

  onMotorClassificacao(motor: string) {
    this.motorClassificacao = motor;
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  formatarDuracao(ms: number): string {
    const totalSeg = Math.round(ms / 1000);
    const min = Math.floor(totalSeg / 60);
    const seg = totalSeg % 60;
    return `${min}:${seg.toString().padStart(2, '0')}`;
  }
}

