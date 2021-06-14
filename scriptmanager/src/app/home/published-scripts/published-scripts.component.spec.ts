import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PublishedScriptsComponent } from './published-scripts.component';

describe('PublishedScriptsComponent', () => {
  let component: PublishedScriptsComponent;
  let fixture: ComponentFixture<PublishedScriptsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PublishedScriptsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PublishedScriptsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
