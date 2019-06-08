import { Component, OnInit } from '@angular/core';
import { FormGroup, FormArray, FormBuilder, Validators, FormControl } from '@angular/forms';
import { TutorialsService } from '../_service/tutorials.service'

@Component({
  selector: 'app-edit-script',
  templateUrl: './edit-script.component.html',
  styleUrls: ['./edit-script.component.sass']
})

export class EditScriptComponent implements OnInit {
  public myForm: FormGroup;
  public rows;

  constructor(private _fb: FormBuilder) { }



  ngOnInit() {
    this.myForm = this._fb.group({
      rows : this._fb.array([
        this.initrow(),
      ])
      });
  }


  initrow() {
    var visualCueData = 'Visual Cue Edit Data'
    var narrationData = 'Narration Edit Data'
    return this._fb.group({
    visualCue: [visualCueData],
    narration: [narrationData]
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
