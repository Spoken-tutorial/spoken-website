import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScriptCommentBoxComponent } from './script-comment-box.component';

describe('ScriptCommentBoxComponent', () => {
  let component: ScriptCommentBoxComponent;
  let fixture: ComponentFixture<ScriptCommentBoxComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScriptCommentBoxComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScriptCommentBoxComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
