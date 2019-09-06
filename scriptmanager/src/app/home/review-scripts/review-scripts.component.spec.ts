import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ReviewScriptsComponent } from './review-scripts.component';

describe('ReviewScriptsComponent', () => {
  let component: ReviewScriptsComponent;
  let fixture: ComponentFixture<ReviewScriptsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ReviewScriptsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ReviewScriptsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
