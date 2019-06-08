import { Component, OnInit } from '@angular/core';
import { FormGroup, FormArray, FormBuilder, Validators, FormControl } from '@angular/forms';
@Component({
  selector: 'app-create-script',
  templateUrl: './create-script.component.html',
  styleUrls: ['./create-script.component.sass']
})

export class CreateScriptComponent implements OnInit {
  public myForm: FormGroup;
  public rows;
  constructor(private _fb: FormBuilder) { 
  }
  ngOnInit() {
  this.myForm = this._fb.group({
  rows : this._fb.array([
    this.initrow(),
  ])
  });
  }
  
  initrow() {
  return this._fb.group({
  visualCue: [''],
  narration: ['']
  });
  }

  addLanguage() {
  const val = <FormArray>this.myForm.controls.rows;
  // controlw.push("this.initlanguage()");
  console.log(this.myForm.controls.rows);
  console.log(this.myForm.controls.languages);
  val.push(this.initrow());
  }

  removeLanguage(i: number) {
  const control = <FormArray>this.myForm.controls.rows;
  control.removeAt(i);
  }
  save(myForm) {
  console.log(this.myForm.value);
  }
  }
