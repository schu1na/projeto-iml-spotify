import { Component, output, signal, ElementRef, HostListener, viewChild, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RecomendacaoService } from '../../services/recomendacao.service';
import { SugestaoMusica } from '../../models/sugestao-musica.model';
import { catchError, debounceTime, distinctUntilChanged, filter, of, Subject, Subscription, switchMap, tap } from 'rxjs';

@Component({
  selector: 'app-search-bar',
  imports: [FormsModule],
  templateUrl: './search-bar.html',
  styleUrl: './search-bar.css',
})
export class SearchBar {
  
  readonly searchQuery = signal('');
  readonly listaSugestoes = signal<SugestaoMusica[]>([]);
  readonly carregandoSugestoes = signal(false);
  readonly showSuggestions = signal(false);
  readonly isFocused = signal(false);
  readonly motorClassificacao = signal<'lightgbm' | 'linear'>('lightgbm');
  readonly filtrarGenero = signal<boolean>(false);

  readonly search = output<SugestaoMusica>();
  readonly filtroGeneroOutput = output<boolean>()
  readonly motorClassificacaoOutput = output<string>()
  
  private readonly inputRef = viewChild<ElementRef>('searchInput');
  
  private searchSubject = new Subject<string>();
  private seachSubscription!: Subscription;
  
  constructor(private recomendacaoService: RecomendacaoService) {}

  ngOnInit(): void {
    this.seachSubscription = this.searchSubject
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),

        tap((termo) => {
          if(termo.length < 3) {
            this.listaSugestoes.set([]);
            this.showSuggestions.set(false);
            this.carregandoSugestoes.set(false);
          } else {
            this.carregandoSugestoes.set(true);
          }
        }),

        filter((termo) => termo.length >= 3),

        switchMap((termo) => 
          this.recomendacaoService.buscarSugestoes(termo).pipe(
            catchError((erro) => {
              console.error('Erro ao buscar sugestões: ', erro)
              this.carregandoSugestoes.set(false)
              this.showSuggestions.set(false)
              return of([]);
            })
          )
        )
      ).subscribe((sugestoes: SugestaoMusica[]) => {
        this.listaSugestoes.set(sugestoes)
        this.showSuggestions.set(sugestoes.length > 0)
        this.carregandoSugestoes.set(false)
      });
  }

  onInputChange(value: string): void {
    this.searchQuery.set(value);
    this.searchSubject.next(value);
  }

  onFocus(): void {
    this.isFocused.set(true);
    if (this.searchQuery().trim().length > 0 && this.listaSugestoes().length > 0) {
      this.showSuggestions.set(true);
    }
  }

  onBlur(): void {
    setTimeout(() => {
      this.isFocused.set(false);
      this.showSuggestions.set(false);
    }, 200);
  }

  onEnter(): void {
    const sugestoesAtuais = this.listaSugestoes(); 
    
    if (sugestoesAtuais && sugestoesAtuais.length > 0) {
      this.selecionarSugestao(sugestoesAtuais[0]);
    } else {
      this.showSuggestions.set(false);
    }
  }

  mudarFiltroGenero() {
    this.filtrarGenero.set(!this.filtrarGenero());
  }

  selecionarSugestao(sugestao: SugestaoMusica): void {
    this.searchQuery.set("");
    this.showSuggestions.set(false);
    // Emite os parâmetros ANTES de emitir a busca,
    // pois Angular processa outputs de forma síncrona —
    // onSearch no pai rodaria com valores antigos se emitíssemos depois.
    this.filtroGeneroOutput.emit(this.filtrarGenero());
    this.motorClassificacaoOutput.emit(this.motorClassificacao());
    this.search.emit(sugestao);
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.showSuggestions.set(false);
    this.inputRef()?.nativeElement?.blur();
  }
}
