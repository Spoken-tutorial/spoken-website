import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateScriptComponent } from './create-script.component';

describe('CreateScriptComponent', () => {
  let component: CreateScriptComponent;
  let fixture: ComponentFixture<CreateScriptComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CreateScriptComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateScriptComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
