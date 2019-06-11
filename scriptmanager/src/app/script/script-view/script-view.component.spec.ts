import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScriptViewComponent } from './script-view.component';

describe('ScriptViewComponent', () => {
  let component: ScriptViewComponent;
  let fixture: ComponentFixture<ScriptViewComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScriptViewComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScriptViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
