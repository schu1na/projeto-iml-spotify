import { Component, inject, signal } from '@angular/core';
import { SearchBar } from './components/search-bar/search-bar';
import { MusicCard, MusicData } from './components/music-card/music-card';
import { ThemeService } from './services/theme.service';

@Component({
  selector: 'app-root',
  imports: [SearchBar, MusicCard],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly themeService = inject(ThemeService);
  protected readonly hasSearched = signal(false);
  protected readonly searchedQuery = signal('');
  protected readonly isLoading = signal(false);

  /** Mock recommended songs — will be replaced by API data */
  protected readonly recommendedSongs = signal<MusicData[]>([]);

  private readonly mockSongs: MusicData[] = [
    {
      title: 'Bohemian Rhapsody',
      artist: 'Queen',
      album: 'A Night at the Opera',
      genre: 'Rock',
      duration: '5:55',
      coverUrl: 'https://i.scdn.co/image/ab67616d0000b273ce4f1737bc8a646c8c4bd25a',
    },
    {
      title: 'Blinding Lights',
      artist: 'The Weeknd',
      album: 'After Hours',
      genre: 'Synthpop',
      duration: '3:20',
      coverUrl: 'https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36',
    },
    {
      title: 'Shape of You',
      artist: 'Ed Sheeran',
      album: '÷ (Divide)',
      genre: 'Pop',
      duration: '3:53',
      coverUrl: 'https://i.scdn.co/image/ab67616d0000b273ba5db46f4b838ef6027e6f96',
    },
    {
      title: 'Bad Guy',
      artist: 'Billie Eilish',
      album: 'WHEN WE ALL FALL ASLEEP, WHERE DO WE GO?',
      genre: 'Electropop',
      duration: '3:14',
      coverUrl: 'https://i.scdn.co/image/ab67616d0000b27350a3147b4edd7701a876c6ce',
    },
    {
      title: 'Levitating',
      artist: 'Dua Lipa',
      album: 'Future Nostalgia',
      genre: 'Disco Pop',
      duration: '3:23',
      coverUrl: 'https://i.scdn.co/image/ab67616d0000b273bd26ede1ae69327010d49946',
    },
  ];

  onSearch(query: string): void {
    this.isLoading.set(true);
    this.searchedQuery.set(query);

    // Simulate API call delay
    setTimeout(() => {
      this.recommendedSongs.set(this.mockSongs);
      this.hasSearched.set(true);
      this.isLoading.set(false);
    }, 800);
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }
}
