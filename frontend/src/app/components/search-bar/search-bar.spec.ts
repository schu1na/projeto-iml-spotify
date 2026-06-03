import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SerchBar } from './search-bar';

describe('SerchBar', () => {
  let component: SerchBar;
  let fixture: ComponentFixture<SerchBar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SerchBar],
    }).compileComponents();

    fixture = TestBed.createComponent(SerchBar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
