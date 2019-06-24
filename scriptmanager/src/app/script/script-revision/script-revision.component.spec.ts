import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScriptRevisionComponent } from './script-revision.component';

describe('ScriptRevisionComponent', () => {
  let component: ScriptRevisionComponent;
  let fixture: ComponentFixture<ScriptRevisionComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScriptRevisionComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScriptRevisionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
