import { ComponentFixture, TestBed } from '@angular/core/testing';
import { describe, it, expect, beforeEach } from 'vitest';

import { HomeViewComponent } from './home-view';

describe('HomeViewComponent', () => {
  let component: HomeViewComponent;
  let fixture: ComponentFixture<HomeViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomeViewComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(HomeViewComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

