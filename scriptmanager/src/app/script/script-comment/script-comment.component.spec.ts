import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScriptCommentComponent } from './script-comment.component';

describe('ScriptCommentComponent', () => {
  let component: ScriptCommentComponent;
  let fixture: ComponentFixture<ScriptCommentComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScriptCommentComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScriptCommentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
