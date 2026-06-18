import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  readonly isDarkMode = signal(true);

  constructor() {
    const saved = localStorage.getItem('theme');
    if (saved === 'light') {
      this.isDarkMode.set(false);
      document.documentElement.classList.add('light-theme');
    }
  }

  toggleTheme(): void {
    const newValue = !this.isDarkMode();
    this.isDarkMode.set(newValue);

    if (newValue) {
      document.documentElement.classList.remove('light-theme');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.add('light-theme');
      localStorage.setItem('theme', 'light');
    }
  }
}
