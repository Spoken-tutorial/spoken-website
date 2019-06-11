import { Component, OnInit } from '@angular/core';
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
  public data: any = [];

  constructor(
      private route: ActivatedRoute,
      public createscriptService: CreateScriptService
    ) { }

  // TODO: implement this method
  public onSaveScript(script: any) {
      console.log(script);
  }

  public getData() {
    this.createscriptService.getScript(this.id).subscribe(
      (res) => {
        for(var i = res['length']; i > 0; i--){
          this.slides.unshift(res[i-1]);
        }
        console.log(this.slides)
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