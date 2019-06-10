import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-script-create',
  templateUrl: './script-create.component.html',
  styleUrls: ['./script-create.component.sass']
})
export class ScriptCreateComponent implements OnInit {
  public slides: any = [];

  constructor() { }

  // TODO: implement this method
  public onSaveScript(script: any) {
    console.log(script);
  }

  ngOnInit() {
  }

}
