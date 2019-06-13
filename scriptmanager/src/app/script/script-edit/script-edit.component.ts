import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';


@Component({
  selector: 'app-script-edit',
  templateUrl: './script-edit.component.html',
  styleUrls: ['./script-edit.component.sass']
})

export class ScriptEditComponent implements OnInit {
  public slides: any = [];
  private id: number;
  private scriptId: number;
  public oldData: any = [];
  public newData: any = [];
  public removedData: any = []

  constructor(
      private route: ActivatedRoute,
      public createscriptService: CreateScriptService
    ) {}

  public onSaveScript(script: any) {
    for (var i = 0; i < script.length; i++) {
      script[i]['order'] = i+1;
      script[i]['script'] = this.scriptId;
    }
  
    for (var i = 0; i < script.length; i++) {
      if (script[i]['id'] == '') {
        this.newData.push(script[i]);
      }
      else {
        this.oldData.push(script[i]);
      }
    }
  
    this.createscriptService.patchScript(
      this.id,
      {
        "delete": this.removedData, 
        "update": this.oldData,
        "insert": this.newData
      }
    ).subscribe(
      console.log,
      console.error
    );

    this.oldData.length = 0;
    this.newData.length = 0;
    this.removedData.length = 0;

  }

  public getData() {
    this.createscriptService.getScript(this.id).subscribe(
      (res) => {
        // for(var i = res['length']; i > 0; i--){
        //   this.slides.unshift(res[i-1]);
        // }
        // this.slides.pop();
        this.slides = res;

        this.scriptId = this.slides[0]['script'];
      }
    );
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.getData();
  }

}