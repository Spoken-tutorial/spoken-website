import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScriptSlideComponent } from './script-slide.component';

describe('ScriptSlideComponent', () => {
  let component: ScriptSlideComponent;
  let fixture: ComponentFixture<ScriptSlideComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScriptSlideComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScriptSlideComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
