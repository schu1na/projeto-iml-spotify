import { Component, input } from '@angular/core';
import { MusicaRecomendada } from '../../models/musica-recomendada.model';


@Component({
  selector: 'app-music-card',
  imports: [],
  templateUrl: './music-card.html',
  styleUrl: './music-card.css',
})
export class MusicCard {
  readonly music = input.required<MusicaRecomendada>();
  readonly index = input<number>(0);

  formatarDuracao(ms: number): string {
    const totalSeg = Math.round(ms / 1000);
    const min = Math.floor(totalSeg / 60);
    const seg = totalSeg % 60;
    return `${min}:${seg.toString().padStart(2, '0')}`;
  }
}
