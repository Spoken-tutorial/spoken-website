import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';
import * as Noty from 'noty';

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
  public removedData: any = [];

  constructor(
      private route: ActivatedRoute,
      public createscriptService: CreateScriptService,
      public router: Router
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
      (res)=>{
        this.router.navigateByUrl("/view/"+this.id);
        new Noty({
          type: 'success',
          layout: 'topRight',
          theme: 'metroui',
          closeWith: ['click'],
          text: 'The script is sucessfully updated!',
          animation: {
              open : 'animated fadeInRight',
              close: 'animated fadeOutRight'
          },
          timeout: 4000,
          killer: true
        }).show();
       },
       (error)=>{
        new Noty({
          type: 'error',
          layout: 'topRight',
          theme: 'metroui',
          closeWith: ['click'],
          text: 'Woops! There seems to be an error.',
          animation: {
              open : 'animated fadeInRight',
              close: 'animated fadeOutRight'
          },
          timeout: 4000,
          killer: true
        }).show();
       }
    );

    this.oldData.length = 0;
    this.newData.length = 0;
    this.removedData.length = 0;

  }

  public getData() {
    this.createscriptService.getScript(this.id).subscribe(
      (res) => {
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