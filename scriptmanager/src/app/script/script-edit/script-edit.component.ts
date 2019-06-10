import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-script-edit',
  templateUrl: './script-edit.component.html',
  styleUrls: ['./script-edit.component.sass']
})
export class ScriptEditComponent implements OnInit {
  public slides: any = [];
  
  constructor() { }

  // TODO: implement this method
  public onSaveScript(script: any) {
    console.log(script);
  }

  ngOnInit() {
  }

}
