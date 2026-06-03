import { Component, input } from '@angular/core';

export interface MusicData {
  title: string;
  artist: string;
  album: string;
  genre: string;
  duration: string;
  coverUrl: string;
}

@Component({
  selector: 'app-music-card',
  imports: [],
  templateUrl: './music-card.html',
  styleUrl: './music-card.css',
})
export class MusicCard {
  readonly music = input.required<MusicData>();
  readonly index = input<number>(0);
}
