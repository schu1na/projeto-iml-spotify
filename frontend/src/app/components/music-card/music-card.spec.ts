import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MusicCard } from './music-card';

describe('MusicCard', () => {
  let component: MusicCard;
  let fixture: ComponentFixture<MusicCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MusicCard],
    }).compileComponents();

    fixture = TestBed.createComponent(MusicCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
