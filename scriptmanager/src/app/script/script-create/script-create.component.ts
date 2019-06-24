import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';
import { UploadFileService } from '../../_service/upload-file.service'
import * as Noty from 'noty';

@Component({
  selector: 'app-script-create',
  templateUrl: './script-create.component.html',
  styleUrls: ['./script-create.component.sass']
})

export class ScriptCreateComponent implements OnInit {
  public slides: any = [];
  private id: number;
  public tutorialName: any;
  
  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService,
    public router: Router,
    public uploadfileService:UploadFileService
  ) { }

  public onFileSave(file:any){
    console.log(file)
    this.uploadfileService.postFile(this.id,file)
    .subscribe(
      res=>{
        console.log(res)
      }
    )

  }
  
  public onSaveScript(script: any) {
    if (script['order'] == '') {
      return // Do nothing
    }
    else {
      for (var i = 0; i < script.length; i++) {
        script[i]['order'] = i + 1;
      }
      this.createscriptService.postScript(
        this.id,
        {
          "details": script
        }
      ).subscribe(
        (res) => {
          this.router.navigateByUrl("/view/" + this.id + "/" + this.tutorialName);
          new Noty({
            type: 'success',
            layout: 'topRight',
            theme: 'metroui',
            closeWith: ['click'],
            text: 'The script is sucessfully created!',
            animation: {
              open: 'animated fadeInRight',
              close: 'animated fadeOutRight'
            },
            timeout: 4000,
            killer: true
          }).show();
        },
        (error) => {
          new Noty({
            type: 'error',
            layout: 'topRight',
            theme: 'metroui',
            closeWith: ['click'],
            text: 'Woops! There seems to be an error.',
            animation: {
              open: 'animated fadeInRight',
              close: 'animated fadeOutRight'
            },
            timeout: 4000,
            killer: true
          }).show();
        }
      );
    }

  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.tutorialName = this.route.snapshot.params['tutorialName']
  }

}
