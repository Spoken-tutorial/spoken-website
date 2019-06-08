import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditScriptComponent } from './edit-script.component';

describe('EditScriptComponent', () => {
  let component: EditScriptComponent;
  let fixture: ComponentFixture<EditScriptComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditScriptComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditScriptComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
