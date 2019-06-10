import { Component, OnInit } from '@angular/core';
import { FormGroup, FormArray, FormBuilder, Validators, FormControl } from '@angular/forms';
import { JsonPipe } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { CreateScriptService } from '../_service/create-script.service'

@Component({
  selector: 'app-create-script',
  templateUrl: './create-script.component.html',
  styleUrls: ['./create-script.component.sass']
})

export class CreateScriptComponent implements OnInit {
  public myForm: FormGroup;
  public rows;
  public sub;
  public id;

  constructor(
    private _fb: FormBuilder,
    private route: ActivatedRoute,
    public createscriptService:CreateScriptService
  ) {}
  
  ngOnInit() {
  
      this.myForm = this._fb.group({
        rows : this._fb.array([
          this.initrow(),
        ])
      });

      this.sub = this.route.params.subscribe(params => {
        this.id = +params['id']; // (+) converts string 'id' to a number
      
      });

  }
 
  initrow() {
    return this._fb.group({
        cue: [''],
        narration: [''],
        order:[]
    });
  }
//add a row
  addRow() {
  
    const val = <FormArray>this.myForm.controls.rows;
    this.myForm.value.rows.forEach(element => {
      console.log(element);
    });
    val.push(this.initrow());
  }
//remove a row
  removeRow(i: number) {
    const control = <FormArray>this.myForm.controls.rows;
    control.removeAt(i);
  
  }
//save all the rows to the database
  save(myForm) {
    //for giving value of order
    for(let i=1;i<=myForm.value.rows.length;i++){
      myForm.value.rows[i-1].order = i;
    }
    var json = {
      "details":this.myForm.value.rows
    }
    var json_str = JSON.stringify(json);
    var json_par = JSON.parse(json_str);
    console.log(json_par);
    
    var res = this.createscriptService.postScript(this.id,json_par).subscribe(
      (res) => console.log(res['status']),
      (err) => console.error('Failed to create script')
    );

  }
  }
