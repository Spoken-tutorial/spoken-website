import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScriptUploadComponent } from './script-upload.component';

describe('ScriptUploadComponent', () => {
  let component: ScriptUploadComponent;
  let fixture: ComponentFixture<ScriptUploadComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScriptUploadComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScriptUploadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
