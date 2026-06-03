import { Component, output, signal, ElementRef, HostListener, viewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-search-bar',
  imports: [FormsModule],
  templateUrl: './search-bar.html',
  styleUrl: './search-bar.css',
})
export class SearchBar {
  readonly searchQuery = signal('');
  readonly isFocused = signal(false);
  readonly showSuggestions = signal(false);

  /** Emitted when the user submits a search query */
  readonly search = output<string>();

  /** Mock suggestions — will be replaced by API calls later */
  readonly suggestions = signal<string[]>([
    'Bohemian Rhapsody — Queen',
    'Blinding Lights — The Weeknd',
    'Shape of You — Ed Sheeran',
    'Bad Guy — Billie Eilish',
    'Stairway to Heaven — Led Zeppelin',
    'Smells Like Teen Spirit — Nirvana',
    'Hotel California — Eagles',
    'Levitating — Dua Lipa',
  ]);

  readonly filteredSuggestions = signal<string[]>([]);

  private readonly inputRef = viewChild<ElementRef>('searchInput');

  onInputChange(value: string): void {
    this.searchQuery.set(value);
    if (value.trim().length > 0) {
      const filtered = this.suggestions().filter(s =>
        s.toLowerCase().includes(value.toLowerCase())
      );
      this.filteredSuggestions.set(filtered);
      this.showSuggestions.set(filtered.length > 0);
    } else {
      this.showSuggestions.set(false);
      this.filteredSuggestions.set([]);
    }
  }

  onFocus(): void {
    this.isFocused.set(true);
    if (this.searchQuery().trim().length > 0 && this.filteredSuggestions().length > 0) {
      this.showSuggestions.set(true);
    }
  }

  onBlur(): void {
    // Delay to allow click on suggestion
    setTimeout(() => {
      this.isFocused.set(false);
      this.showSuggestions.set(false);
    }, 200);
  }

  selectSuggestion(suggestion: string): void {
    this.searchQuery.set(suggestion);
    this.showSuggestions.set(false);
    this.search.emit(suggestion);
  }

  onSubmit(): void {
    if (this.searchQuery().trim()) {
      this.showSuggestions.set(false);
      this.search.emit(this.searchQuery().trim());
    }
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.showSuggestions.set(false);
    this.inputRef()?.nativeElement?.blur();
  }
}
