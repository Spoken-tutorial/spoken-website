import { Component, OnInit } from '@angular/core';


@Component({
  selector: 'app-script-edit',
  templateUrl: './script-edit.component.html',
  styleUrls: ['./script-edit.component.sass']
})
export class ScriptEditComponent implements OnInit {
  public slides: any = [];
  
  public data = [];

  constructor() { }

  // TODO: implement this method
  public onSaveScript(script: any) {
      console.log(script);
  }

  ngOnInit() {
    this.data = this.getData();
    console.log(this.data.length)
    for (var i = 0; i < this.data.length; i++) { 
      this.slides.push(this.data[i]);
    }
  }

  getData() {
    return [
      { 'cue': 'Dummy Data 1', 'narration': 'Dummy Data A' },
      { 'cue': 'Dummy Data 2', 'narration': 'Dummy Data B' },
      { 'cue': 'Dummy Data 4', 'narration': 'Dummy Data D' },
    ];

    // this.createscriptService.getScripts(fid).subscribe(
    //   (res) => this.tutorials = res,
    //   (err) => {
    //     console.log('Failed to fetch tutorial categories');
    //     console.error(err);
    //   }
    // );
  }


}